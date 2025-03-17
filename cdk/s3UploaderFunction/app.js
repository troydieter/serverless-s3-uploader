'use strict'

const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3')
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner')
const crypto = require('crypto')
require('dotenv').config() // Enables .env support for local testing

// Initialize S3 Client
const s3 = new S3Client({ region: process.env.AWS_REGION || 'us-east-1' })

// Main Lambda entry point
exports.handler = async (event) => {
  try {
    const result = await getUploadURL(event)
    console.log('Generated Upload URL:', result)
    return result
  } catch (error) {
    console.error('Error generating upload URL:', error)
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal Server Error' }),
      headers: { 'Access-Control-Allow-Origin': '*' }
    }
  }
}

const getUploadURL = async function(event) {
  if (!process.env.UploadBucket) {
    throw new Error('Missing required environment variable: UploadBucket')
  }

  const actionId = crypto.randomUUID() // Generates a unique file name
  const contentType = event?.queryStringParameters?.contentType || 'application/octet-stream';

  const s3Params = {
    Bucket: process.env.UploadBucket,
    Key: `${actionId}.jpg`,
    ContentType: contentType
  }

  console.log('S3 Params:', s3Params)

  try {
    const command = new PutObjectCommand(s3Params)
    const uploadURL = await getSignedUrl(s3, command, { expiresIn: 300 }) // 5-minute expiration

    return {
      statusCode: 200,
      isBase64Encoded: false,
      headers: { 'Access-Control-Allow-Origin': '*' },
      body: JSON.stringify({
        uploadURL,
        photoFilename: `${actionId}.jpg`
      })
    }
  } catch (error) {
    console.error('Error generating signed URL:', error)
    throw error
  }
}
