import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { createProject, CreateProjectRequest } from '../api/client'

function CreateProject() {
  const [formData, setFormData] = useState<CreateProjectRequest>({
    name: '',
    description: '',
    requirements_text: '',
  })

  const mutation = useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      alert('Project created successfully!')
      setFormData({ name: '', description: '', requirements_text: '' })
    },
    onError: (error: any) => {
      alert(`Error: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(formData)
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Create New Project</h1>
          <p className="mt-2 text-sm text-gray-700">
            Describe your project requirements and let AI agents build it for you
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-8 space-y-6 max-w-2xl">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
            Project Name *
          </label>
          <input
            type="text"
            id="name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
            placeholder="my-awesome-project"
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <input
            type="text"
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
            placeholder="Short description of your project"
          />
        </div>

        <div>
          <label htmlFor="requirements" className="block text-sm font-medium text-gray-700">
            Requirements *
          </label>
          <textarea
            id="requirements"
            required
            rows={8}
            value={formData.requirements_text}
            onChange={(e) => setFormData({ ...formData, requirements_text: e.target.value })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-3 py-2 border"
            placeholder="Describe what you want to build...\n\nExample:\n- REST API for user management\n- Authentication with JWT\n- PostgreSQL database\n- Docker deployment"
          />
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {mutation.isPending ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default CreateProject
