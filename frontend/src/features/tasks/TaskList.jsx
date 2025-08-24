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