// SignIn.js
import React, { useState } from "react";
import { Link, useHistory } from "react-router-dom";
import "./SignIn.css";
import api from "../../api";
import loginImg from "./login.svg";
import UserProfile from "../profile/UserProfile";

const SignIn = () => {
  const history = useHistory();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post("/login", formData);
      const { access_token } = response.data.message;
      localStorage.setItem("accessToken", access_token);
      alert("Login Successfully")
      history.push("/")
    } catch (error) {
      alert("Error login:", error.response.data.detail);
    }
  };

  return (
    <div className="signin-container">
      <div className="signin-image">
        {/* Your image component goes here */}
        <img src={loginImg} alt="Sign Up Image" width="600" height="400" />
      </div>
      <div className="signin-form">
        <h2>Sign In</h2>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              placeholder="Enter your email"
              onChange={handleChange}
              required
            />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              placeholder="Enter your password"
              onChange={handleChange}
              required
            />
          </div>

          <div className="signin-footer">
            <p>
              Don't have an account? <Link to="/signup/">Sign Up</Link>
            </p>
          </div>
          <button type="submit">Sign In</button>
        </form>
      </div>
    </div>
  );
};

export default SignIn;
