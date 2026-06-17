-- 1. Tabla de Organizaciones (Multi-tenancy)
CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;

-- 2. Tabla de Miembros de la Organización
CREATE TABLE IF NOT EXISTS public.organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member' CHECK (role IN ('admin', 'member')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(org_id, user_id)
);
ALTER TABLE public.organization_members ENABLE ROW LEVEL SECURITY;

-- 3. Tabla de Plantillas de Mensajes (Normalización 3NF)
CREATE TABLE IF NOT EXISTS public.message_templates (
    id SERIAL PRIMARY KEY,
    org_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    params_hash TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(org_id, params_hash)
);
ALTER TABLE public.message_templates ENABLE ROW LEVEL SECURITY;

-- 4. Actualizar tabla existente de Cobranzas
ALTER TABLE public.registros_cobranza 
ADD COLUMN IF NOT EXISTS org_id UUID,
ADD COLUMN IF NOT EXISTS template_id INT;

ALTER TABLE public.registros_cobranza ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- 5. POLÍTICAS DE SEGURIDAD (RLS)
-- ==========================================

-- Organizations: Solo miembros pueden ver su organización
CREATE POLICY "Usuarios pueden ver su organización" ON public.organizations
FOR SELECT USING (
    id IN (SELECT org_id FROM public.organization_members WHERE user_id = auth.uid())
);

-- Organization Members: Solo miembros pueden ver otros miembros de su org
CREATE POLICY "Miembros pueden ver otros miembros de su org" ON public.organization_members
FOR SELECT USING (
    org_id IN (SELECT org_id FROM public.organization_members WHERE user_id = auth.uid())
);

-- Message Templates: Aislamiento estricto por organización
CREATE POLICY "Solo miembros de la org pueden ver sus templates" ON public.message_templates
FOR ALL USING (
    org_id IN (SELECT org_id FROM public.organization_members WHERE user_id = auth.uid())
);

-- Registros de Cobranza: Aislamiento estricto por organización
CREATE POLICY "Solo miembros de la org pueden ver sus registros" ON public.registros_cobranza
FOR ALL USING (
    org_id IN (SELECT org_id FROM public.organization_members WHERE user_id = auth.uid())
);

-- ==========================================
-- 6. CUSTOM ACCESS TOKEN HOOK (Para inyectar org_id en el JWT)
-- ==========================================
CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_org_id UUID;
    claims jsonb;
BEGIN
    claims := event->'claims';
    
    SELECT org_id INTO v_org_id 
    FROM public.organization_members 
    WHERE user_id = (claims->>'sub')::uuid 
    LIMIT 1;

    IF v_org_id IS NOT NULL THEN
        claims := jsonb_set(claims, '{org_id}', to_jsonb(v_org_id));
        event := jsonb_set(event, '{claims}', claims);
    END IF;

    RETURN event;
END;
$$;

GRANT EXECUTE ON FUNCTION public.custom_access_token_hook TO supabase_auth_admin;
REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook FROM PUBLIC;