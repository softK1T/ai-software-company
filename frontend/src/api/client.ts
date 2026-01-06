import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ProjectTemplate {
  id: string
  name: string
  version: string
  description: string | null
  tags: string[]
  config_patch: Record<string, any>
  is_system: boolean
  created_at: string
  updated_at: string | null
}

export interface TemplatesResponse {
  templates: ProjectTemplate[]
  total: number
}

export const getTemplates = async (): Promise<TemplatesResponse> => {
  const { data } = await apiClient.get<TemplatesResponse>('/api/templates')
  return data
}

export interface CreateProjectRequest {
  name: string
  description?: string
  requirements_text: string
  template_id?: string
  config_overrides?: Record<string, any>
}

export const createProject = async (project: CreateProjectRequest) => {
  const { data } = await apiClient.post('/api/projects', project)
  return data
}
