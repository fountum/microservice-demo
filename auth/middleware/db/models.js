const { Sequelize, DataTypes } = require('sequelize');
const sequelize = new Sequelize('mysql://auth_svc:WORMSandDIRTandSAND@localhost:3306/auth_db');

// Define modes to use in other files
models = {
    User: {
    // Model attributes are defined here
    username: {
      type: DataTypes.STRING,
      allowNull: false,
    },
    password: {
      type: DataTypes.STRING,
      allowNull: false,
    },
  }
}

const defineModels = (conn) => {
    const User = conn.define(
        'User',
        models.User
    )
    return User
}


module.exports = {
    models,
    defineModels
};