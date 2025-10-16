const express = require("express");
const session = require("express-session");
const passport = require("./middleware/passport");
const app = express();
const path = require("path");
const ejsLayouts = require("express-ejs-layouts");
const reminderController = require("./controller/reminder_controller");
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
// app.get("/reminders", reminderController.list);

// app.get("/reminder/new", reminderController.new);

// app.get("/reminder/:id", reminderController.listOne);

// app.get("/reminder/:id/edit", reminderController.edit);

// app.post("/reminder/", reminderController.create);

// // Implement this yourself
// app.post("/reminder/update/:id", reminderController.update);

// // Implement this yourself
// app.post("/reminder/delete/:id", reminderController.delete);





app.listen(3001, function () {
  console.log(
    "Server running. Visit: localhost:3001/reminders in your browser 🚀"
  );
});
