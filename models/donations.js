const mongoose  = require('mongoose')

const DonationSchema = new mongoose.Schema({
    donorName: String,
    foodType: String,
    quantity: Number,
    pickupLocation: String,
    expirationDate: String,
    status: { type: String, default: "available" }, // available, picked, delivered
    createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Donation',DonationSchema)//creates a collection named donations and that can be accessed by the name Donation