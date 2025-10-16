const { Sequelize, DataTypes } = require('sequelize');

const sequelize = new Sequelize('mysql://auth_svc:WORMSandDIRTandSAND@localhost:3306/world')
const {models, defineModels} = require('./models.js')

const User = defineModels(sequelize)
User.drop()