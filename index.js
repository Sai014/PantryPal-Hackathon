const express = require('express');
const dotenv = require('dotenv');
const connectDB = require('./config/db.js');
const route = require('./routes/routings.js');
const cors = require('cors');
const path = require('path');

dotenv.config();
connectDB();

const app = express();
app.use(express.json());
app.use(cors());

// Serve the frontend
app.use(express.static(path.join(__dirname, 'public')));

// API Routes
app.use('/api/donations', route);

app.listen(5000, () => {
    console.log('LISTENING ON PORT 5000....');
});

app.post('/api/donations', (req, res) => {
    const { name, foodType, quantity, pickupAddress } = req.body;

    if (!name || !foodType || !quantity || !pickupAddress) {
        return res.status(400).json({ message: "All fields are required" });
    }

    console.log("New Donation:", req.body);
    res.status(201).json({ message: "Donation received successfully!" });
});
