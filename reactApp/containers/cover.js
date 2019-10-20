import React from "react";
import { Link } from "react-router-dom";


const Cover = function() {
  return (
    <div className="coverPage">
      <div>
        <h1 style={{textAlign:"center"}}>OUR NAME</h1>
        <p>Welcome to OUR NAME, a platform for XXX</p>
        </div>
      
      <div className="buttonContainer">
        <Link to="/signup">
          <button style={styles.authbutton} className="ghost-button">Sign Up</button>
        </Link>
        <Link to="/login">
          <button style={styles.authbutton} className="ghost-button">Log in</button>
        </Link>
      </div>
    </div>
  );
};

export default Cover;

const styles = {
  authbutton: {
    marginLeft: "5px",
    marginRight: "5px",
    width: "200px"
  }
}
