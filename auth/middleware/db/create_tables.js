const { Sequelize } = require('sequelize');
const sequelize = new Sequelize(process.env.MYSQL_CONN);
const {defineModels} = require('./models.js')

const createTables = async () => {
    await sequelize.sync({ force: true });
    console.log('All models were synchronized successfully.');
}

defineModels(sequelize)
createTables()
