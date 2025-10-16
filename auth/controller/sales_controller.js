const axios = require('axios');

let saleController = {
  stats: async (req, res) => {
    if (!req.user){
      res.redirect('/login');
      return;
    } 
    
    const stats_res = await axios.get('http://localhost:8100/stats');
    if (stats_res.status != 200) {
      console.log(stats_res.statusText);
      return;
    }
    res.render("sales/stats", {stats: stats_res.data});
  },

  // render page for submitting report
  report: (req, res) => {
    if (!req.user){
      res.redirect('/login');
      return;
    } 
    res.render("sales/report");
  },

  // post sales report
  submitReport: async (req, res) => {
    if (!req.user){ 
      res.redirect('/login');
      return;
    } 

    axios.post('http://localhost:8080/sales', {
      customers : parseInt(req.body.customers),
      cookies_sold : parseInt(req.body.cookies),
      income : parseInt(req.body.income)
    });
    

    res.redirect("/sales/stats");
  },
};

module.exports = salesController;
