const { Sequelize } = require('sequelize');
const sequelize = new Sequelize('mysql://auth_svc:WORMSandDIRTandSAND@localhost:3306/world');
const {defineModels} = require('./models.js')

const createTables = async () => {
    await sequelize.sync({ force: true });
    console.log('All models were synchronized successfully.');
}

defineModels(sequelize)
createTables()
