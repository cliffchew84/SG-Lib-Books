import { initializeApp } from "firebase/app";
import { getMessaging } from "firebase/messaging";
import {
	PUBLIC_FIREBASE_APPID,
	PUBLIC_FIREBASE_APIKEY,
	PUBLIC_FIREBASE_PROJECTID,
	PUBLIC_FIREBASE_AUTHDOMAIN,
	PUBLIC_FIREBASE_MEASUREMENTID,
	PUBLIC_FIREBASE_STORAGEBUCKET,
	PUBLIC_FIREBASE_MESSAGINGSENDERID,
} from '$env/static/public';

const firebaseConfig = {
	apiKey: PUBLIC_FIREBASE_APIKEY,
	authDomain: PUBLIC_FIREBASE_AUTHDOMAIN,
	projectId: PUBLIC_FIREBASE_PROJECTID,
	storageBucket: PUBLIC_FIREBASE_STORAGEBUCKET,
	messagingSenderId: PUBLIC_FIREBASE_MESSAGINGSENDERID,
	appId: PUBLIC_FIREBASE_APPID,
	measurementId: PUBLIC_FIREBASE_MEASUREMENTID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Cloud Messaging and get a reference to the service
export const messaging = getMessaging(app);

