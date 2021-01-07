( () => {

  var BidMachine = window.BidMachine || {};
  BidMachine.map = BidMachine.map || {};

  var authToken;

  const signinUrl = 'html/signin.html';

  BidMachine.authToken.then( ( token ) => {

    if ( token ) {
      authToken = token;
      console.log( 'Token: ' + authToken );
    }
    else
      window.location.href = signinUrl;

  } ).catch( ( error ) => {
    alert( error )
    window.location.href = signinUrl;
  } );


  // BUTTON SIGN OUT

  const signOutBtn = document.querySelector( '#signout' );

  signOutBtn.addEventListener( 'click', ( e ) => {

    e.preventDefault();

    userPool = new AmazonCognitoIdentity.CognitoUserPool(
      {
        UserPoolId: _config.cognito.userPoolId,
        ClientId: _config.cognito.userPoolClientId
      }
    );

    BidMachine.signOut = () => {
        userPool.getCurrentUser().signOut();
    };

    window.location.href = '../index.html';
      
  });


  // Load Data

  window.onload = async () => {

    await fetch( _config.api.invokeUrl + '/wordsapi', {
      method: "GET",
      headers: {
        "Authorization": authToken,
        'Content-Type': 'application/json'
      }

    })
    .then( response => response.json() )
    .then( json => {

      json.forEach( item => {

        listWords( item[ 'word' ] );

      });
  
    }).catch( err => console.error(err) )

  }



  // FORM WORDS

  const wordsResourceAPI = '/wordsapi';
  const fileResourceAPI = '/fileuploadapi';

  document.querySelector('#msg').style.display = 'none';

  const cadastrar = document.querySelector( '#cadastrar' );  

  cadastrar.addEventListener( 'click', async () => {
     
    let palavra = document.querySelector('#nome').value;
    
    if( palavra !== '' ) {

      let data = {
        palavra: palavra
      }

      await fetch( _config.api.invokeUrl + wordsResourceAPI, {
        method: "POST",
        mode: 'cors',

        headers: {
          "Authorization": authToken,  
          'Content-Type': 'application/json',
        },

        body: JSON.stringify( data )
        })
        .then( response => response.json() )
        .then( json => { 
          console.log(json)

          if( json['ResponseMetadata']['HTTPStatusCode'] === 200 ) {
          
            document.querySelector('#nome').value = '';
            msg( 0, 'sucess' );
            
            setTimeout( "window.location.href = 'home.html';" , 1400); 
          }
        
        })
        .catch( err => {
          console.error(err);
          msg( 4, 'errors' )
        
        } );
  
    }
    else {
      
      msg( 1, 'errors' )
      
    }

  });



  const listWords = ( word ) => {

    var nome      = document.createElement( 'li' ),
        actionDel = document.createElement( 'li' ),
        fragment  = document.createDocumentFragment(),
        del       = document.createElement( 'input' ),
        container = document.createElement( 'ul' ),
        edit      = document.createElement( 'input' );

    del.setAttribute( 'name', 'deletar' );
    del.setAttribute( 'type', 'button' );
    del.setAttribute( 'id', 'del_' + word.split(" ").join("") );
    del.setAttribute( 'class', 'del' );
    
    
    edit.setAttribute( 'name', 'editar' );
    edit.setAttribute( 'type', 'button' );
    edit.setAttribute( 'id', 'edit_' + word.split(" ").join("") );
    edit.setAttribute( 'class', 'edit' );


    actionDel.setAttribute( 'class', 'btnAction' );
    nome.setAttribute( 'class', 'dados' );


    container.setAttribute( 'id', word.split(" ").join("") );
    container.setAttribute( 'class', 'allData' );

    nome.appendChild( document.createTextNode( word ) );

    actionDel.appendChild( del );
    actionDel.appendChild( edit );

    fragment.appendChild( nome );
    fragment.appendChild( actionDel );

    container.appendChild( fragment );

    let list = document.querySelector('#list');
    list.appendChild( container );

    //BUTTON DELETE

    let deleteBtn = document.querySelector( '#del_' + word.split(" ").join("") );

    deleteBtn.addEventListener( 'click', async ( e ) => {

      console.log('Delete');
     
      e.preventDefault();

      let data = { palavra: word }


      await fetch( _config.api.invokeUrl + wordsResourceAPI, {
        method: "DELETE",
        mode: 'cors',

        headers: {
          "Authorization": authToken,  
          'Content-Type': 'application/json',
        },

        body: JSON.stringify( data )
        })
        .then( response => response.json() )
        .then( json => { 
          console.log(json)

          if( json['ResponseMetadata']['HTTPStatusCode'] === 200 ) {
          
            msg( 1, 'sucess' );
            
            setTimeout( "window.location.href = 'home.html';" , 1400); 
          }
        
        })
        .catch( err => {
          console.error(err);
          msg( 4, 'errors' );
        });
    } );


    // BUTTON EDIT

    let editBtn = document.querySelector( '#edit_' + word.split(" ").join("") );
    editBtn.addEventListener( 'click', ( e ) => {

      editContato( word )

    });

  };

  const editContato = ( editWord ) => {

    var editar    = document.createElement( 'input' ),
        cadastrar = document.createElement( 'input' );

    editar.setAttribute( 'type', 'button' );
    editar.setAttribute( 'class', 'cadastrar' );
    editar.setAttribute( 'id', 'atualizar' );
    editar.setAttribute( 'value', 'Atualizar' );

    cadastrar.setAttribute( 'value', 'Cadastrar' );
    cadastrar.setAttribute( 'type', 'button' );
    cadastrar.setAttribute( 'class', 'cadastrar' );
    cadastrar.setAttribute( 'id', 'cadastrar' );


    document.querySelector('#nome').value = editWord;
    document.querySelector('#cadastrar').remove();
    document.querySelector('.container__input-word').appendChild( editar );


    // BUTTON UPDATE

    let salvarBtn = document.querySelector( '#atualizar' );

    salvarBtn.addEventListener( 'click', async ( e ) => {

      e.preventDefault();

      let newWord = document.querySelector( '#nome' ).value;

      console.log( 'Current: ' + editWord );
      console.log( 'New: ' + newWord );

      if ( newWord !== '' ) {
        
        let data = { 
          palavra: editWord,
          novaPalavra: newWord
         }

        await fetch( _config.api.invokeUrl + wordsResourceAPI, {
          method: "PUT",
          mode: 'cors',
  
          headers: {
            "Authorization": authToken,  
            'Content-Type': 'application/json',
          },
  
          body: JSON.stringify( data )
          })
          .then( response => response.json() )
          .then( json => { 
            console.log(json)
  
            if( json['ResponseMetadata']['HTTPStatusCode'] === 200 ) {
            
              msg( 2, 'sucess' );
              
              setTimeout( "window.location.href = 'home.html';" , 1400); 
            }
          
          })
          .catch( err => {
            console.error(err);
            msg( 3, 'errors' );
          });

      }  
    } );
 };


  const msg = ( idx , typ ) => {
    var err     = ['Prencha Todos os Campos Corretamente', 'Preencha os Campos Vazios','Usuário Já Cadastrado', 'Erro desconhecido, por favor tente novamente!', 'Nenhum arquivo selecionado!'];
    var success = ['Cadastrado Com Sucesso','Removido com Sucesso', 'Atualizado com Sucesso', 'Arquivo enviado com Sucesso'];

    const msg = document.querySelector('#msg');

    msg.className = typ;
    msg.style.marginBottom = '30px';
    msg.style.display = 'block';

    if( typ === 'errors') msg.innerHTML = err[idx] +'!';
    else msg.innerHTML = success[idx] +'!';
    
    setTimeout('document.getElementById("msg").style.display = "none"', 2000);
};




// UPLOAD BUTTON

const btnSubmit = document.querySelector( '.container__upload-button' );

btnSubmit.addEventListener( 'click', async ( e ) => {

  let files = document.querySelector( '.uploadBtn' ).files;

  let file = files[0];

  console.log( file )

  if ( file ) {

    var formData = new FormData();
  
    let blobFile = new Blob( [ file ], { type: 'text/xml' } );
  
    formData.append( 'blobFile', blobFile, files[0].name )
  
    await fetch( _config.api.invokeUrl + fileResourceAPI, {
      method: "POST",
      mode: 'cors',
  
      headers: {
        "Authorization": authToken,  
        'Content-Type': 'text/xml',
      },
  
      body:  formData
      })
      .then( response => response.json() )
      .then( json => { 
        console.log(json)
  
        if( json['ResponseMetadata']['HTTPStatusCode'] === 200 ) {
      
          msg( 3, 'sucess' );
        
        }
      
      })
      .catch( err => {
        console.error(err);
        msg( 3, 'errors' );
      });
  } 
  else {
    msg( 4, 'errors' );
  }


});

} )();