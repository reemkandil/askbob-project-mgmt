// frontend/src/features/auth/AuthPage.jsx
import React, { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>AskBob Project Management</h1>
          <p>Streamline your projects with intelligent task management</p>
        </div>

        <div className="auth-content">
          {isLogin ? (
            <LoginForm onSwitchToRegister={() => setIsLogin(false)} />
          ) : (
            <RegisterForm onSwitchToLogin={() => setIsLogin(true)} />
          )}
        </div>

        <div className="auth-footer">
          <p>&copy; 2024 AskBob Project Management. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;