const passport = require("passport");
const LocalStrategy = require("passport-local").Strategy;
const userController = require("../controller/userController");
const { Sequelize } = require('sequelize');
const {models, defineModels} = require('./db/models.js')

// db stuff
const sequelize = new Sequelize('mysql://auth_svc:WORMSandDIRTandSAND@localhost:3306/world');
const User = defineModels(sequelize)

// const { PrismaClient } = require('@prisma/client');
// const db = new PrismaClient()

// PRE EXISTING STUFF
const localLogin = new LocalStrategy(
  {
    usernameField: "username",
    passwordField: "password",
  },
  async (username, password, done) => {
    const user = await userController.getUserByEmailIdAndPassword(username, password);
    return user
      ? done(null, user)
      : done(null, false, {
          message: "Your login details are not valid. Please try again",
        });
  }
);

const localSignup = new LocalStrategy(
  {
    usernameField: "username",
    passwordField: "password",
    passReqToCallback: true,
  },
  async (req, username, password, done) => {
    // check if user exists
    const user = await User.findOne({
      where: {
        username: username.toLowerCase(),
      }
    })
    if (user) {
      return done(null, false, {
        message: `username taken: ${username}`
      })
    }

    // create user in db
    const newUser = await User.create({
        username: username.toLowerCase(),
        password: password, // HASHING
    })

    return done(null, newUser);
  }
)

passport.serializeUser(function (user, done) {
  done(null, user.id);
});

passport.deserializeUser(async function (id, done) {
  let user = await userController.getUserById(id);
  if (user) {
    done(null, user); // creates req.user
  } else {
    done({ message: "User not found" }, null);
  }
});

module.exports = passport.use('local', localLogin);
module.exports = passport.use('local-signup',localSignup);
