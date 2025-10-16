const express = require("express");
const session = require("express-session");
const passport = require("./middleware/passport");
const app = express();
const path = require("path");
const ejsLayouts = require("express-ejs-layouts");
const salesController = require("./controller/sales_controller");
const authController = require("./controller/auth_controller");

app.use(express.static(path.join(__dirname, "public")));

app.use(
  session({
    secret: "secret",
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: false,
      maxAge: 24 * 60 * 60 * 1000,
    },
  })
);

app.use(passport.initialize());
app.use(passport.session());

app.use(express.urlencoded({ extended: false }));

app.set("view engine", "ejs");
app.use(ejsLayouts);

// Routes start here, re work them
// auth routes
app.get("/login", authController.login)
app.get("/register", authController.register);
app.post("/register", authController.registerSubmit);
app.post("/login", authController.loginSubmit);

app.get("/sales/stats", salesController.stats);

app.get("/sales/report", salesController.report);

app.post("/sales/report", salesController.submitReport);





app.listen(3001, function () {
  console.log(
    "Server running. Visit: localhost:3001/reminders in your browser 🚀"
  );
});
