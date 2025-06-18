const express = require('express')
const route = express.Router()
const { addDonation, getAvailableDonations, notifyNGOs} = require("../controllers/donationController")
const{ findNearestNGO } = require("../controllers/ngoController")

route.post('/',addDonation)

route.get('/available',getAvailableDonations)

route.post('/notify',notifyNGOs)

route.post('/findNGO',findNearestNGO)

module.exports = route

