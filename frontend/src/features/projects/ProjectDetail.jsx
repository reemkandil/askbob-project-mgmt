// frontend/src/features/projects/ProjectDetail.jsx
import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { projectsApi, tasksApi } from '../../lib/api';
import TaskList from '../tasks/TaskList';
import CreateTaskForm from '../tasks/CreateTaskForm';

const ProjectDetail = () => {
  const { id } = useParams();
  const [showCreateTaskForm, setShowCreateTaskForm] = useState(false);
  const queryClient = useQueryClient();

  const { data: project, isLoading: projectLoading, error: projectError } = useQuery(
    ['project', id],
    () => projectsApi.getById(id).then(res => res.data)
  );

  const { data: tasks, isLoading: tasksLoading } = useQuery(
    ['tasks', id],
    () => tasksApi.getByProject(id).then(res => res.data),
    { enabled: !!id }
  );

  const updateProjectMutation = useMutation(
    ({ id, data }) => projectsApi.update(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['project', id]);
      },
    }
  );

  const handleStatusChange = (newStatus) => {
    updateProjectMutation.mutate({
      id,
      data: { status: newStatus }
    });
  };

  if (projectLoading) return <div className="loading">Loading project...</div>;
  if (projectError) return <div className="error">Error loading project: {projectError.message}</div>;

  return (
    <div className="project-detail">
      <div className="project-detail-header">
        <Link to="/" className="back-link">← Back to Projects</Link>
        
        <div className="project-info">
          <h1>{project.name}</h1>
          <div className="project-meta">
            <select 
              value={project.status} 
              onChange={(e) => handleStatusChange(e.target.value)}
              className="status-select"
            >
              <option value="planning">Planning</option>
              <option value="in_progress">In Progress</option>
              <option value="on_hold">On Hold</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <span className="created-date">
              Created: {new Date(project.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>

      {project.description && (
        <div className="project-description">
          <p>{project.description}</p>
        </div>
      )}

      <div className="tasks-section">
        <div className="tasks-header">
          <h2>Tasks</h2>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateTaskForm(true)}
          >
            Add Task
          </button>
        </div>

        {showCreateTaskForm && (
          <CreateTaskForm
            projectId={id}
            onClose={() => setShowCreateTaskForm(false)}
            onSuccess={() => {
              setShowCreateTaskForm(false);
              queryClient.invalidateQueries(['tasks', id]);
            }}
          />
        )}

        {tasksLoading ? (
          <div className="loading">Loading tasks...</div>
        ) : (
          <TaskList tasks={tasks} projectId={id} />
        )}
      </div>
    </div>
  );
};

export default ProjectDetail;