
let main = document.getElementById('main');

main.addEventListener("change", (event) => {
    if (event.target.tagName != 'INPUT' || event.target.value != 'task') return;

    fetch('/complete_task', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'id' : event.target.form.id.value
        })
    }).then(function(response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                console.log(response);
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })    .catch(function(error) {
        console.log(error);
    });
});

main.addEventListener("click", (event) => {
    if (event.target.tagName != 'BUTTON' || event.target.value != 'delete') return;
    event.target.form.parentElement.parentElement.parentElement.remove()
    fetch('/delete', {
        headers : {
            'Content-Type' : 'application/json'
        },
        method : 'POST',
        body : JSON.stringify( {
            'id' : event.target.form.id.value
        })
    }).then(function(response){
        if(response.ok) {
            response.json()
            .then(function(response) {
                console.log(response);
            });
        }
        else {
            throw Error('Something went wrong');
        }
    })    .catch(function(error) {
        console.log(error);
    });
});