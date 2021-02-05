var BidMachine = window.BidMachine || {};

(() => {

    const signinUrl = '../index.html';
    const homeUrl = '../html/home.html';
    const verifyUrl = '../html/verify.html';

    if ( !window._config )
        alert("Error js/config.js file missing, check the S3 Web Application Bucket for the file");

    const poolData = {
        UserPoolId: _config.cognito.userPoolId,
        ClientId: _config.cognito.userPoolClientId
    };

    const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

    if (typeof AWSCognito !== 'undefined') {
        AWSCognito.config.region = _config.cognito.region;
    }

    BidMachine.signOut = function signOut() {
        userPool.getCurrentUser().signOut();
    };

    BidMachine.authToken = new Promise((resolve, reject) => {
        var cognitoUser = userPool.getCurrentUser();

        if (cognitoUser) {
            cognitoUser.getSession((err, session) => {
                if (err) {
                    reject(err);
                } else if (!session.isValid()) {
                    resolve(null);
                } else {
                    resolve(session.getIdToken().getJwtToken());
                }
            });
        } else {
            resolve(null);
        }
    });




    /*
     * Cognito User Pool functions
     */

    function register(email, password, onSuccess, onFailure) {
        var dataEmail = {
            Name: 'email',
            Value: email
        };
        var attributeEmail = new AmazonCognitoIdentity.CognitoUserAttribute(dataEmail);

        userPool.signUp(toUsername(email), password, [attributeEmail], null,
            function signUpCallback(err, result) {
                if (!err) {
                    onSuccess(result);
                } else {
                    onFailure(err);
                }
            }
        );
    }

    function signin(email, password, onSuccess, onFailure) {
        var authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails({
            Username: toUsername(email),
            Password: password
        });

        var cognitoUser = createCognitoUser(email);
        cognitoUser.authenticateUser(authenticationDetails, {
            onSuccess: onSuccess,
            onFailure: onFailure
        });
    }

    function verify(email, code, onSuccess, onFailure) {
        createCognitoUser(email).confirmRegistration(code, true, (err, result) => {
            if (!err) {
                onSuccess(result);
            } else {
                onFailure(err);
            }
        });
    }

    function createCognitoUser(email) {
        return new AmazonCognitoIdentity.CognitoUser({
            Username: toUsername(email),
            Pool: userPool
        });
    }

    function toUsername(email) {
        return email.replace('@', '-at-');
    }



    /*
     * Frontend functions 
     */

    // SIGN IN
    const signinForm = document.querySelector('#signinForm');

    if (signinForm) {

        signinForm.addEventListener("submit", (e) => {
            e.preventDefault();

            const email = document.querySelector('#emailInputSignin').value;
            const password = document.querySelector('#passwordInputSignin').value;

            signin(email, password, () => {

                    console.log('Successfully Logged In');
                    window.location.href = homeUrl;
                },
                (err) => {
                    alert(err);
                }
            );

        });
    }



    // SIGN UP
    const registrationForm = document.querySelector('#registrationForm');

    if (registrationForm) {
        registrationForm.addEventListener("submit", (e) => {
            e.preventDefault();

            const email = document.querySelector('#emailInputRegister').value;
            const password = document.querySelector('#passwordInputRegister').value;
            const password2 = document.querySelector('#password2InputRegister').value;


            amazonRegex = /[a-z]*[._-]*[a-z]*(@amazon.com)/g;

            if ( email.match( amazonRegex ) ) {
                
                const onSuccess = (result) => {
                    var cognitoUser = result.user;
                    console.log('user name is ' + cognitoUser.getUsername());
                    alert('Registration successful. Please check your email for your verification code');
                    window.location.href = verifyUrl;
                };

                const onFailure = (err) => {
                    alert(err);
                };

                if (password === password2)
                    register(email, password, onSuccess, onFailure);
                else
                    alert('Passwords do not match');
            }
            
            else {

                alert( 'Amazon Users only' )

            }


        });
    }


    // VERIFY
    const verifyForm = document.querySelector('#verifyForm');

    if (verifyForm) {

        verifyForm.addEventListener("submit", (e) => {

            e.preventDefault();

            const email = document.querySelector('#emailInputVerify').value;
            const code = document.querySelector('#codeInputVerify').value;

            const defaultUserSettings = '/defaultUserSettings';

            verify(email, code,
                async ( result ) => {
                    console.log('call result: ' + result);
                    console.log('Successfully verified');
                    
                    let data = { "email": email }
                    
                    await fetch( _config.api.invokeUrl +  defaultUserSettings, {
                        method: "POST",
                        mode: 'cors',
                    
                        headers: {
                          'Content-Type': 'application/json',
                        },
                    
                        body:  JSON.stringify( data )
                        })
                        .then( response => response.json() )
                        .then( json => { 
                            // console.log(json)
                            alert('Verification successful. You will now be redirected to the login page.');
                            window.location.href = signinUrl;
                         })
                        .catch( err => { console.error(err); });
  
                },

                ( err ) => alert(err)
                
            );

        });
    }


})();