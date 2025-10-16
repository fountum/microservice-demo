const { Sequelize } = require('sequelize');
const sequelize = new Sequelize(process.env.MYSQL_CONN);
const {models, defineModels} = require('../middleware/db/models.js')
const crypto = require('crypto');

const User = defineModels(sequelize)

const getUserByEmailIdAndPassword = async (username, password) => {
  const hash = crypto.createHash('sha256');
  hash.update(password);
  const hashed_password = hash.digest('hex');
  const user = await User.findOne(
    {
      where: {
        username: username.toLowerCase(),
        password: hashed_password 
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
