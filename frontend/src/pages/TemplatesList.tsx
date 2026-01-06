import { useQuery } from '@tanstack/react-query'
import { getTemplates } from '../api/client'

function TemplatesList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['templates'],
    queryFn: getTemplates,
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        Error loading templates: {(error as Error).message}
      </div>
    )
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Project Templates</h1>
          <p className="mt-2 text-sm text-gray-700">
            Choose a template to start your AI-powered software project
          </p>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {data?.templates.map((template) => (
          <div
            key={template.id}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="p-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">{template.name}</h3>
                <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                  v{template.version}
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-500">{template.description}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {template.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              {template.is_system && (
                <div className="mt-3">
                  <span className="inline-flex items-center text-xs text-green-700">
                    ✓ System Template
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {data?.total === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No templates available. Run seed script to create default templates.</p>
        </div>
      )}
    </div>
  )
}

export default TemplatesList
