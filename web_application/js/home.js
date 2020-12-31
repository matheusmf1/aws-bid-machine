( () => {

  var BidMachine = window.BidMachine || {};
  BidMachine.map = BidMachine.map || {};

  var authToken;

  BidMachine.authToken.then( ( token ) => {

    if ( token ) {
      authToken = token;
      console.log( 'oooi: ' + authToken );
    }
    else
      window.location.href = '/signin.html';

  } ).catch( ( error ) => {
    alert( error )
    window.location.href = '/signin.html';
  } );


  const buttonTest = document.querySelector('#test');

  buttonTest.addEventListener( 'click', () => {

    console.log('kjhgkjhmnb');
 
    let _data = {
      title: "foo",
      body: "bar", 
      userId:1
    }
    
    fetch( _config.api.invokeUrl + '/bidmachineapi', {
      method: "POST",
      headers: {
        "Content-type": "application/json",
        "Authorization": authToken,
      },
      mode: 'no-cors',
      body: JSON.stringify( _data )
    })
    .then( response => response.json() )
    .then( json => console.log(json) )
    .catch( err => console.log(err) )

  } );
} )();