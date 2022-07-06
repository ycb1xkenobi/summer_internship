import React from "react";
import {IoCloseCircleSharp, IoHammerSharp} from 'react-icons/io5';

class User extends React.Component {
    user = this.props.user
    render(){
        return(
            <div className="user">
                <IoCloseCircleSharp className="delete-icon"/>
                <IoHammerSharp className="edit-icon"/>
                <h3>{this.user.id} {this.user.email}</h3>
                <h4>Password: {this.user.password}</h4>
            </div>
        )
    }
}

export default User