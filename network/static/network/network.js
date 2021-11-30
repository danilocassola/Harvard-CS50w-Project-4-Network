document.addEventListener('DOMContentLoaded', function() {

    let path = location.pathname.substring(1);
    if (path == "") {
        path = "all";
    }

    if (document.querySelector('#new_post')){

        // By default, submit button is disabled
        document.querySelector('#submit').disabled = true;

        // Enable button only if there is text in the input field
        document.querySelector('#content').onkeyup = () => {
            if (document.querySelector('#content').value.trim() != "")
                document.querySelector('#submit').disabled = false;
            else
                document.querySelector('#submit').disabled = true;
        };
    }
});


// csrftoken
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


function edit_post(post_id) {
    fetch(`/posts_api/id/${post_id}`)
    .then(response => response.json())
    .then(post => {
        document.querySelector(`#post_${post_id}`).innerHTML =
            `<div class="post">
                <p><textarea class="form-control" id="content_post" rows="3">${post.content}</textarea> </p>
            </div>
            <div class="save_post_btn right">
                <button type="button" id="edit_post_${ post.id }"  onclick="save_post(${ post.id })" class="btn btn-primary btn-sm">Save</button>
            </div>
            `;

        document.querySelector(`#edit_post_${post_id}`).style.display = 'none';
    })
    .catch(error => {
        console.log("error: ", error);
    });
}


function save_post(post_id){
    const content_post = document.querySelector("#content_post").value;
    const request = new Request(
    `/posts_api/save/${post_id}`,
    {headers: {'X-CSRFToken': csrftoken}}
    );

    // Save the content
    fetch(request, {
    method: 'PUT',
    body: JSON.stringify({
            content: content_post
        })
    })
    .then(response => response.json())
    .then(post => {
        document.querySelector(`#post_${post_id}`).innerHTML = post.content;
        document.querySelector(`#edit_post_${post_id}`).style.display = 'block';
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


function like(post_id) {
    const request = new Request(
    `/posts_api/like/${post_id}`,
    {headers: {'X-CSRFToken': csrftoken}}
    );

    fetch(request, {
        method: 'PUT',
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector(`#likespost_${post_id}`).innerHTML = data.likes;
        document.querySelector(`#heartpost_${post_id}`).className = data.heart_icon;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
