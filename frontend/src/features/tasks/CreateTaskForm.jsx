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