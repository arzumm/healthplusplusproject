import React, { useState } from "react";
import { Link, Redirect } from "react-router-dom";

function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [isSignup, setIsSignup] = useState(false);

  const signup = e => {
    e.preventDefault();

    fetch("http://localhost:3000/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json" //are these headers right
      },
      body: JSON.stringify({
        email,
        password,
        firstName,
        lastName
      })
    })
      .then(response => response.json())
      .then(responseJson => {
        console.log(" post /signup response", responseJson);
        if (responseJson.success) {
          setIsSignup(true);
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  if (isSignup) {
    return <Redirect to="/login" />;
  } else {
    return (
      <div
        style={{
          justifyContent: "center",
          alignItems: "center",
          height: "100%",
          display: "flex",
          flexDirection: "column"
        }}
      >
        <h3 style={{ textAlign: "center" }}>Register</h3>
        <form className="signupForm" onSubmit={e => signup(e)}>
          <div className="form-row">
            <div className="form-group col-md-6">
              <label>Email</label>
              <input
                className="form-control"
                type="text"
                name="email"
                value={email}
                placeholder="email"
                onChange={e => setEmail(e.target.value)}
              />
            </div>
            <div className="form-group col-md-6">
              <label>Password</label>
              <input
                className="form-control"
                type="password"
                name="password"
                value={password}
                placeholder="password"
                onChange={e => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group col-md-6">
              <label> First Name</label>
              <input
                className="form-control"
                type="text"
                name="firstName"
                value={firstName}
                placeholder="Enter your first name"
                onChange={e => setFirstName(e.target.value)}
              />
            </div>
            <div className="form-group col-md-6">
              <label> Last Name</label>
              <input
                className="form-control"
                type="text"
                name="lastName"
                value={lastName}
                placeholder="Enter your last name"
                onChange={e => setLastName(e.target.value)}
              />
            </div>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <input
              style={{ width: "20%" }}
              className="ghost-button"
              type="submit"
              value="Sign up!"
            />
            <Link to="/login" style={{ textAlign: "right" }}>
              Login Here!
            </Link>
          </div>
        </form>
      </div>
    );
  }
}

export default Signup;
