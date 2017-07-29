import React from 'react';
import CInP from './cinp';
import ConfigDialog from './ConfigDialog';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Site extends React.Component
{
  state = {
      site_list: [],
      site: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { site_list: [], site: null } );
    this.update( newProps );
  }

  update( props )
  {
    if( props.id !== undefined )
    {
      props.detailGet( props.id )
       .then( ( result ) =>
        {
          var data = result.data;
          data.parent = CInP.extractIds( data.parent )[0];
          data.config_values = Object.keys( data.config_values ).map( ( key ) => ( [ key, data.config_values[ key ] ] ) );
          this.setState( { site: data } );
        } );
    }
    else
    {
      props.listGet()
        .then( ( result ) =>
        {
          var site_list = [];
          for ( var name in result.data )
          {
            var site = result.data[ name ];
            name = CInP.extractIds( name )[0];
            site_list.push( { name: name,
                              description: site.description,
                              created: site.created,
                              updated: site.updated,
                            } );
          }

          this.setState( { site_list: site_list } );
        } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var site = this.state.site;
      return (
        <div>
          <h3>Site Detail</h3>
          { site !== null &&
            <div>
              <ConfigDialog getConfig={ this.props.getConfig } uri={ '/api/v1/Site/Site:' + this.props.id + ':' } />
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ site.name }</td></tr>
                  <tr><th>Parent</th><td><Link to={ '/site/' + site.parent }>{ site.parent }</Link></td></tr>
                  <tr><th>Description</th><td>{ site.description }</td></tr>
                  <tr><th>Config Values</th><td><table><thead/><tbody>{ site.config_values.map( ( value ) => ( <tr key={ value[0] }><th>{ value[0] }</th><td>{ value[1] }</td></tr> ) ) }</tbody></table></td></tr>
                  <tr><th>Created</th><td>{ site.created }</td></tr>
                  <tr><th>Updated</th><td>{ site.updated }</td></tr>
                </tbody>
              </table>
            </div>
          }
        </div>
      );
    }

    return (
      <Table selectable={ false } multiSelectable={ false }>
        <TableHead>
          <TableCell>Name</TableCell>
          <TableCell>Description</TableCell>
          <TableCell>Created</TableCell>
          <TableCell>Updated</TableCell>
        </TableHead>
        { this.state.site_list.map( ( item ) => (
          <TableRow key={ item.name } >
            <TableCell><Link to={ '/site/' + item.name }>{ item.name }</Link></TableCell>
            <TableCell>{ item.description }</TableCell>
            <TableCell>{ item.created }</TableCell>
            <TableCell>{ item.updated }</TableCell>
          </TableRow>
        ) ) }
      </Table>
    );

  }
};

export default Site;
