/*var email=document.forms['loginform']['email'];
var password=document.forms['loginform']['pwd'];

//error display objects
var email_error=document.getElementById['email_span'];
var pwd_error=document.getElementById['pwd_span'];

//event listeners
email.addEvetListener("blur",emailVerify, true);
password.addEvetListener("blur",passwordVerify, true);

function validatelogin(){
  //email validation
 if(email.value==""){
  email.style.border="1px solid red";
  email_error.textContent="Email is required";
  email.focus();
  return false;
 }
 //password validation
  if(password.value==""){
  password.style.border="1px solid red";
  pwd_error.textContent="Password is required";
  password.focus();
  return false;
 }
}
//event handler function
function emailVerify(){
  if(email.value!=""){
    email.style.border="1px solid #5E6E66";
    email_error.innerHTML="";
    return true;
  }
}

function passwordVerify(){
  if(password.value!=""){
    password.style.border="1px solid #5E6E66";
    email_error.innerHTML="";
    return true;
  }
}
*/
$(document).ready(function(){
  $('form').on('submit', function(validateform){
    $.ajax({
      data:{
        email:$('#email').val(),
        pwd:$('#pwd').val(),
      },
      type: 'POST', 
      url: '/login'
    })
    .done(function(data){
      if (data.failure){
        $('#failure').text(data.failure).show();
        $('#success').hide();

      }else{
        $('#success').text(data.success).show();
        $('#failure').hide();

      }

    });
    validateform.preventDefault();
  });

});