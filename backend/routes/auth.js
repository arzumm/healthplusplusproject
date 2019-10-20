const express = require("express");
const router = express.Router();
const { User } = require("../models/user");


module.exports = function(passport, hash) {
    router.post("/signup", (req, res) => {
      console.log(req.body);
      const newUser = new User({
        firstName: req.body.firstName,
        lastName: req.body.lastName,
        email: req.body.email,
        password: hash(req.body.password)
      });
      console.log(newUser);
      newUser.save(function(err, result) {
        if (err) {
          res.json({ success: false, error: "Unable to save the user" });
        } else {
          res.json({ success: true, error: "" });
        }
      });
    });


    router.post(
        "/login",
        passport.authenticate("local", {
          successRedirect: "/login/success",
          failureRedirect: "/login/failure"
          // failureFlash: true
        })
      );
      router.get("/login/failure", function(req, res) {
        res.status(401).json({
          success: false,
          error: "Incorrect username or password."
        });
      });
    
      router.get("/login/success", function(req, res) {
        const { username, _id } = req.user;
        res.json({
          success: true,
          user: { username, _id }
        });
      });

      router.get("/logout", function(req, res) {
        req.logout();
        res.json({
          success: true,
          error: ""
        });
      });
    
    //   router.use((req, res, next) => {
    //     if (!req.user) {
    //       res.status(401).json({
    //         success: false,
    //         error: "Not authorized"
    //       });
    //       return;
    //     }
    //     next();
    //   });
    
      return router;

};