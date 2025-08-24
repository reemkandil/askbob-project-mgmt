// frontend/src/lib/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Projects API
export const projectsApi = {
  getAll: () => api.get('/projects'),
  getById: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
};

// Tasks API
export const tasksApi = {
  getByProject: (projectId) => api.get(`/projects/${projectId}/tasks`),
  create: (projectId, data) => api.post(`/projects/${projectId}/tasks`, data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
};

export default api;

// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import ProjectList from './features/projects/ProjectList';
import ProjectDetail from './features/projects/ProjectDetail';
import './App.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <header className="App-header">
            <h1>AskBob Project Management</h1>
          </header>
          <main>
            <Routes>
              <Route path="/" element={<ProjectList />} />
              <Route path="/projects/:id" element={<ProjectDetail />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;

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

// frontend/src/features/projects/CreateProjectForm.jsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from 'react-query';
import { projectsApi } from '../../lib/api';

const CreateProjectForm = ({ onClose, onSuccess }) => {
  const { register, handleSubmit, formState: { errors }, reset } = useForm();

  const createMutation = useMutation(
    (data) => projectsApi.create(data),
    {
      onSuccess: () => {
        reset();
        onSuccess();
      },
    }
  );

  const onSubmit = (data) => {
    createMutation.mutate(data);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>Create New Project</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="project-form">
          <div className="form-group">
            <label htmlFor="name">Project Name *</label>
            <input
              type="text"
              id="name"
              {...register('name', { 
                required: 'Project name is required',
                maxLength: { value: 200, message: 'Name must be less than 200 characters' }
              })}
              className={errors.name ? 'error' : ''}
            />
            {errors.name && <span className="error-text">{errors.name.message}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              rows="3"
              {...register('description')}
              placeholder="Optional project description..."
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={createMutation.isLoading}
              className="btn btn-primary"
            >
              {createMutation.isLoading ? 'Creating...' : 'Create Project'}
            </button>
          </div>

          {createMutation.error && (
            <div className="error-text">
              Error creating project: {createMutation.error.response?.data?.detail || createMutation.error.message}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default CreateProjectForm;

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

// frontend/src/features/tasks/TaskList.jsx
import React from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { tasksApi } from '../../lib/api';

const TaskList = ({ tasks, projectId }) => {
  const queryClient = useQueryClient();

  const updateTaskMutation = useMutation(
    ({ id, data }) => tasksApi.update(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks', projectId]);
      },
    }
  );

  const deleteTaskMutation = useMutation(
    (id) => tasksApi.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks', projectId]);
      },
    }
  );

  const handleStatusChange = (taskId, newStatus) => {
    updateTaskMutation.mutate({
      id: taskId,
      data: { status: newStatus }
    });
  };

  const handleDelete = (taskId) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      deleteTaskMutation.mutate(taskId);
    }
  };

  if (!tasks || tasks.length === 0) {
    return (
      <div className="empty-state">
        <p>No tasks yet. Add a task to get started!</p>
      </div>
    );
  }

  const tasksByStatus = tasks.reduce((acc, task) => {
    if (!acc[task.status]) acc[task.status] = [];
    acc[task.status].push(task);
    return acc;
  }, {});

  const statusColumns = [
    { key: 'todo', label: 'To Do' },
    { key: 'in_progress', label: 'In Progress' },
    { key: 'in_review', label: 'In Review' },
    { key: 'done', label: 'Done' }
  ];

  return (
    <div className="task-board">
      {statusColumns.map(({ key, label }) => (
        <div key={key} className="task-column">
          <h3 className="column-header">{label}</h3>
          <div className="task-list">
            {(tasksByStatus[key] || []).map((task) => (
              <div key={task.id} className="task-card">
                <div className="task-header">
                  <h4>{task.title}</h4>
                  <span className={`priority priority-${task.priority}`}>
                    {task.priority}
                  </span>
                </div>
                
                {task.description && (
                  <p className="task-description">{task.description}</p>
                )}
                
                <div className="task-meta">
                  {task.due_date && (
                    <span className="due-date">
                      Due: {new Date(task.due_date).toLocaleDateString()}
                    </span>
                  )}
                </div>

                <div className="task-actions">
                  <select
                    value={task.status}
                    onChange={(e) => handleStatusChange(task.id, e.target.value)}
                    className="status-select-sm"
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="in_review">In Review</option>
                    <option value="done">Done</option>
                  </select>
                  
                  <button
                    className="btn btn-danger btn-xs"
                    onClick={() => handleDelete(task.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default TaskList;

// frontend/src/features/tasks/CreateTaskForm.jsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from 'react-query';
import { tasksApi } from '../../lib/api';

const CreateTaskForm = ({ projectId, onClose, onSuccess }) => {
  const { register, handleSubmit, formState: { errors }, reset } = useForm();

  const createMutation = useMutation(
    (data) => tasksApi.create(projectId, data),
    {
      onSuccess: () => {
        reset();
        onSuccess();
      },
    }
  );

  const onSubmit = (data) => {
    // Convert due_date to ISO string if provided
    if (data.due_date) {
      data.due_date = new Date(data.due_date).toISOString();
    }
    createMutation.mutate(data);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>Create New Task</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="task-form">
          <div className="form-group">
            <label htmlFor="title">Task Title *</label>
            <input
              type="text"
              id="title"
              {...register('title', { 
                required: 'Task title is required',
                maxLength: { value: 200, message: 'Title must be less than 200 characters' }
              })}
              className={errors.title ? 'error' : ''}
            />
            {errors.title && <span className="error-text">{errors.title.message}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              rows="3"
              {...register('description')}
              placeholder="Optional task description..."
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="priority">Priority</label>
              <select id="priority" {...register('priority')}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="due_date">Due Date</label>
              <input
                type="date"
                id="due_date"
                {...register('due_date')}
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={createMutation.isLoading}
              className="btn btn-primary"
            >
              {createMutation.isLoading ? 'Creating...' : 'Create Task'}
            </button>
          </div>

          {createMutation.error && (
            <div className="error-text">
              Error creating task: {createMutation.error.response?.data?.detail || createMutation.error.message}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default CreateTaskForm;