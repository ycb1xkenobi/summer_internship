import React from "react";
import User from "./User"

class Users extends React.Component{
    constructor(props) {
        super(props)
        this.state ={
            users: [        
                {id: 1, email: "test1@mail.com", password: 1234, logged: false},
                {id: 2, email: "test2@mail.com", password: 1234, logged: false}
            ]
        }
    }
    render() {
        if (this.state.users.length > 0)
            return(
                <div>
                    {this.state.users.map((el) => (
                        <User key = {el.id} user = {el}/>
                        ))}
                </div>
            )
        else
            return(
                <div className="user">  
                    <h3>no users</h3>
                </div>
        )
    }
}

export default Users