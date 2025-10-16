const { Sequelize, DataTypes } = require('sequelize');

const sequelize = new Sequelize(process.env.MYSQL_CONN)
const {models, defineModels} = require('./models.js')

const User = defineModels(sequelize)
User.drop()