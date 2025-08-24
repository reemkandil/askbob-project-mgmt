// frontend/src/features/projects/ProjectList.jsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Link } from 'react-router-dom';
import { projectsApi } from '../../lib/api';
import CreateProjectForm from './CreateProjectForm';

const ProjectList = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const queryClient = useQueryClient();

  const { data: projects, isLoading, error } = useQuery(
    'projects',
    () => projectsApi.getAll().then(res => res.data)
  );

  const deleteMutation = useMutation(
    (id) => projectsApi.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('projects');
      },
    }
  );

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div className="loading">Loading projects...</div>;
  if (error) return <div className="error">Error loading projects: {error.message}</div>;

  return (
    <div className="project-list">
      <div className="project-list-header">
        <h2>Projects</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateForm(true)}
        >
          Create New Project
        </button>
      </div>

      {showCreateForm && (
        <CreateProjectForm 
          onClose={() => setShowCreateForm(false)}
          onSuccess={() => {
            setShowCreateForm(false);
            queryClient.invalidateQueries('projects');
          }}
        />
      )}

      <div className="projects-grid">
        {projects?.map((project) => (
          <div key={project.id} className="project-card">
            <div className="project-card-header">
              <h3>
                <Link to={`/projects/${project.id}`} className="project-link">
                  {project.name}
                </Link>
              </h3>
              <span className={`status status-${project.status}`}>
                {project.status.replace('_', ' ')}
              </span>
            </div>
            
            {project.description && (
              <p className="project-description">{project.description}</p>
            )}
            
            <div className="project-card-footer">
              <small>Created: {new Date(project.created_at).toLocaleDateString()}</small>
              <button 
                className="btn btn-danger btn-sm"
                onClick={() => handleDelete(project.id)}
                disabled={deleteMutation.isLoading}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {projects?.length === 0 && (
        <div className="empty-state">
          <p>No projects yet. Create your first project to get started!</p>
        </div>
      )}
    </div>
  );
};

export default ProjectList;