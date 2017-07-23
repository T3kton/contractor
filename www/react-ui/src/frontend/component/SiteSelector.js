import React from 'react';
import { Dropdown } from 'react-toolbox';

class SiteSelector extends React.Component
{
  state = {
    site_list: []
  }

  handleChange = ( value ) =>
  {
    this.props.onSiteChange( value );
  }

  componentDidMount()
  {
    this.props.siteListGetter()
      .then( ( result ) =>
      {
        var site_list = [];
        for ( var site in result.data )
        {
          site_list.push( { value: site, label: result.data[ site ].description } );
        }

        this.setState( { site_list: site_list } );
        this.props.onSiteChange( site_list[0].value );
      } );
  }

  render()
  {
    return (
<Dropdown title='Current Site' icon='cloud' auto onChange={this.handleChange} source={this.state.site_list} value={this.props.curSite} allowBlank={false} required={true}/>
);
  }
};

export default SiteSelector;
