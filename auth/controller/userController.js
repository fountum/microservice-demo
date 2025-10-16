const { Sequelize } = require('sequelize');
const sequelize = new Sequelize('mysql://auth_svc:WORMSandDIRTandSAND@localhost:3306/world');
const {models, defineModels} = require('../middleware/db/models.js')

const User = defineModels(sequelize)

const getUserByEmailIdAndPassword = async (username, password) => {
  const user = await User.findOne(
    {
      where: {
        username: username.toLowerCase(),
        password: password //HASH!
      }
    }
  );
  if (user) return user;
  return null;
};

// remove?
const getUserById = async (id) => {
  const user = await User.findOne({
    where: {id:id}
  })
  if (user) return user;
  return null;
};

module.exports = {
  getUserByEmailIdAndPassword,
  getUserById,
};
