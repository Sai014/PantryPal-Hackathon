const{Client} = require('@googlemaps/google-maps-services-js')
const NGOs = require('../models/ngo.js')
require('dotenv').config();
let latitude;
let longitude;
const client = new Client({})

async function findNearestNGO(req,res){
    const { pickupAddress } = req.body;
    const response = await client.geocode({
        params : {
            address: pickupAddress,
            key : process.env.GOOGLE_API_KEY
        }
    })
    const locations = response.data.results[0].geometry.location
    latitude = locations.lat
    longitude = locations.lng
    try{
        if(!latitude || !longitude){
        res.status(500).json({error:"INVALID LOCATION"})
        }
    

        const response = await client.placesNearby({
            params:{
                location : `${latitude},${longitude}`,
                radius : 5000,
                keyword : 'food bank',
                key : process.env.GOOGLE_API_KEY,
            },
        });

        const ngos = response.data.results.map((place) => ({
            name :place.name,
            location:{
                type:'Point',
                coordinates :[place.geometry.location.lat,place.geometry.location.lng],
            },
            contact:place.formatted_phone_number
        }));

        await NGOs.insertMany(ngos,{ordered:false}).catch((err) => {console.log(err)})

        res.status(200).json({ message: "NGOs fetched and stored", ngos });
        }
        catch(err){
            res.status(500).json({error:"COULD NOT SEND MESSAGE"})
        }
};  
module.exports = {findNearestNGO}







