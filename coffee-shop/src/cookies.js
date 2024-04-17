import React, { useState, useEffect } from 'react';
import { useCookies } from 'react-cookie';
import './cookies.css';

// mhhh cookies are very good
export const Cookies = () => {

  const [cookie, setCookie] = useCookies(['SID']);
  const [cookieExists, setCookieExists] = useState(false);

  useEffect(() => {
    const checkCookie = () => {
      const cookieValue = cookie['SID'];

      if (cookieValue) {
        setCookieExists(true);
      }
    }

    checkCookie();
  }, [cookie]);

  const acceptCookies = async () => {
    try { const response = await fetch('/api/session', {
        method: 'GET',
    })
    
    const data = response.json();
    setCookie(data.cookie)
    } catch(error) {
      console.log(error)
    }
  };

  return (
    <>
    {cookieExists ? (<></>) : (
      <div className='cookies'>
        <h1>Cookies!</h1>
        <p>Accept cookies in order to shop on our awesome website</p>
        <button className="cookieBtn" onClick={acceptCookies}>Accept Cookies</button>
      </div>
    )}
    </>
  );
};
