const { Sequelize, DataTypes } = require('sequelize');
const sequelize = new Sequelize('mysql://auth_svc:WORMSandDIRTandSAND@localhost:3306/world');

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

// `sequelize.define` also returns the model
// console.log(User === sequelize.models.User); // true

// await sequelize.sync({ force: true });
// console.log('All models were synchronized successfully.');

module.exports = {
    models,
    defineModels
};