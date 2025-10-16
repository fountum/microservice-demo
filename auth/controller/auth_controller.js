const passport = require("../middleware/passport");

let authController = {
  login: (req, res) => {
    res.render("auth/login");
  },

  register: (req, res) => {
    res.render("auth/register");
  },

  loginSubmit: 
    passport.authenticate("local", {
    successRedirect: "https://youtube.com",
    failureRedirect: "/login",
  }),

  registerSubmit:
    passport.authenticate('local-signup', {
      successRedirect: '/reminders',
      failureRedirect: '/register',
  }),

  ensureAdmin: (req, res, next) => {
    if (req.user && req.user.admin) {
      return next();
    } else {
      res.redirect("/auth/login");
    }
  },
};

module.exports = authController;
