import React from "react";


class AddUser extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            email: "",
            password: "",
            teacher: false
        }
    }
    render(){
        return(
            <form>
                <input placeholder="email" onChange={(event => this.setState({email: event.target.value}))} />
                <input placeholder="password" onChange={(event => this.setState({password: event.target.value}))}/>
    
                <button type="button">Register</button>
            </form>
    )
  }  
}

export default AddUser