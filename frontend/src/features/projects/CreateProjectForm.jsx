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