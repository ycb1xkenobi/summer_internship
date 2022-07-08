import React from "react";



class AddUser extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            email: "",
            role: "",
        }
    }

    ButtonPressed = () => {
        // let email = this.state.email;
        // let role = this.state.role;
        console.log("Done")
        console.log(this.state.email)    
    }

    render(){
        return(
            <form>
                <input placeholder={this.props.textOne} onChange={(event => this.setState({email: event.target.value}))} key = "BoxOne"/>
                <input placeholder={this.props.textTwo} onChange={(event => this.setState({role: event.target.value}))} key = "BoxTwo"/>
    
                <button type="button" onClick={this.ButtonPressed}> Register </button>
            </form>
    )
  }  
}


export default AddUser
