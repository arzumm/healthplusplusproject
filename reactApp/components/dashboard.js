import React, {useState, useEffect} from 'react'; 

function Dashboard() {
    const [data, setData] = useState([]);

    function Submit(e) {
        e.preventDefault();
        fetch('http://localhost:3000/submit', {
            method: 'POST', 
            headers:{
                "Content-Type": "application/json"
            },
            credentials: "include", 
            redirect: 'follow', 
            body: JSON.stringify({
                content: data
            })
        })
        .then (response => {
            return response.json;
        })
        .then(responseJson => {
            console.log(responseJson.success); 
            if (responseJson.success)  {
                alert('Record saved!')
            }
        })
        .catch(err => console.log(err));
    }

    return (
        <div>
            <h2 style = {{textAlign: "center"}}> Upload a photo </h2>
            <div> 
                {/* add a upload a photo button that sets data using setData  */}
                <input type = "submit" 
                value = 'Submit'
                onClick={e => {
                    Submit(e);
                }}
                />
            </div>
        </div>
    )
}

export default Dashboard;