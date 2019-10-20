// import React from "react";
// import { BrowserRouter, Route, Link } from "react-router-dom";
// import "./App.css";
// import Cover from "./containers/Cover";
// import Login from "./components/Login";
// // import Dashboard from "./containers/Dashboard";

// function App() {
//   return (
//     <BrowserRouter>
//       {/* <Route path="/" exact={true} component={Cover} /> */}
//       <Route path="/" exact={true} component={Signup} />
//       <Route path="/login" exact={true} component={Login} />
//       {/* <Route path="/dashboard" exact={true} component={Dashboard} /> */}
//     </BrowserRouter>
//   );
// }

// export default App;


import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Route, Link } from "react-router-dom";
import './index.css';
import Signup from './components/signup';


function App() {
    return (
        <Signup/>
        // <BrowserRouter>
        //         <Route path="/" exact={true} component={Signup} />
        // </BrowserRouter>
    );
}


ReactDOM.render(<App />, document.getElementById('root'));