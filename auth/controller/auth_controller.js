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
    successRedirect: "/sales/stats",
    failureRedirect: "/login",
  }),

  registerSubmit:
    passport.authenticate('local-signup', {
      successRedirect: '/login',
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
