const Donation  = require('../models/donations.js')
const twilio = require('twilio')
const {Client} = require('@googlemaps/google-maps-services-js')
require('dotenv').config()
// const {storeDonation,getAllDonations} = require('../blockchain.js')

//let pickupAddress;
async function addDonation(req,res){
    try{
        const{donorName,foodType,quantity,pickupLocation,expirationDate} = req.body
        //pickupAddress = pickupLocation
        const donation = new Donation({
        donorName,
        foodType,
        quantity,
        pickupLocation,
        expirationDate,
    })
    await donation.save()
    notifyNGOs()
    // const txHash = await storeDonation(donorName,foodType,quantity,pickupLocation,expirationDate)
    res.status(200).json({message :'DONATION ADDED TO DB SUCCESSFULLY'})
    }
    catch(err){
        res.status(404).json({message:err})
    }
    
}

async function getAvailableDonations(req,res){
    try{
        const availableDonations = await Donation.find({status:'available'})
        // const blockchainDonations = await getAllDonations();
        res.status(200).json(availableDonations,blockchainDonations);
    } catch (error) {
        res.status(500).json({ error: "Failed to fetch donations" });
    }
}
async function notifyNGOs(req,res){
    const latestDonation = await Donation.findOne().sort({_id : -1});
    const client = twilio(process.env.TWILIO_SID,process.env.TWILIO_AUTH_TOKEN)
    try{
            await client.messages.create({
            body:`NEW DONATION AVAILABLE AT ${latestDonation.pickupLocation}`,
            from : +18782156891,
            to : +919379706369
        })
        res.status(200).json({message:'MESSAGE SENT TO NGO'})
    }
    catch(err){
        res.status(500).json({message:err})
        console.log(err)
    }
}
module.exports = {addDonation,getAvailableDonations,notifyNGOs}
    