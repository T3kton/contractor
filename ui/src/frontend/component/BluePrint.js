import React from 'react';
import CInP from './cinp';
import ConfigDialog from './ConfigDialog';
import ScriptDialog from './ScriptDialog';
import { Table, TableHead, TableRow, TableCell } from 'react-toolbox';
import { Link } from 'react-router-dom';


class BluePrint extends React.Component
{
  state = {
      blueprintF_list: [],
      blueprintS_list: [],
      blueprint: null
  };

  componentDidMount()
  {
    this.update( this.props );
  }

  componentWillReceiveProps( newProps )
  {
    this.setState( { blueprintF_list: [], blueprintS_list: [], blueprint: null } );
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
          data.parent_list = data.parent_list.map( ( parent ) =>
          {
            if ( parent.startsWith( '/api/v1/BluePrint/StructureBluePrint' ) )
            {
              return 's/' + CInP.extractIds( parent )[0];
            }
            else if ( parent.startsWith( '/api/v1/BluePrint/FoundationBluePrint' ) )
            {
              return 'f/' + CInP.extractIds( parent )[0];
            }
          } );
          data.scripts = data.scripts.map( ( entry ) => ( CInP.extractIds( entry )[0] ) );
          data.config_values = Object.keys( data.config_values ).map( ( key ) => ( [ key, data.config_values[ key ] ] ) );
          this.setState( { blueprint: data } );
        } );
    }
    else
    {
      props.listGetF()
        .then( ( result ) =>
        {
          var blueprint_list = [];
          for ( var name in result.data )
          {
            var blueprint = result.data[ name ];
            name = CInP.extractIds( name )[0];
            blueprint_list.push( { name: name,
                              description: blueprint.description,
                              created: blueprint.created,
                              updated: blueprint.updated,
                            } );
          }

          this.setState( { blueprintF_list: blueprint_list } );
        } );
        props.listGetS()
          .then( ( result ) =>
          {
            var blueprint_list = [];
            for ( var name in result.data )
            {
              var blueprint = result.data[ name ];
              name = CInP.extractIds( name )[0];
              blueprint_list.push( { name: name,
                                description: blueprint.description,
                                created: blueprint.created,
                                updated: blueprint.updated,
                              } );
            }

            this.setState( { blueprintS_list: blueprint_list } );
          } );
    }
  }

  render()
  {
    if( this.props.id !== undefined )
    {
      var blueprint = this.state.blueprint;
      return (
        <div>
          <h3>BluePrint Detail</h3>
          { blueprint !== null &&
            <div>
              <ConfigDialog getConfig={ this.props.getConfig } uri={ '/api/v1/BluePrint/BluePrint:' + this.props.id + ':' } />
              <table>
                <thead/>
                <tbody>
                  <tr><th>Name</th><td>{ blueprint.name }</td></tr>
                  <tr><th>Parents</th><td><ul>{ blueprint.parent_list.map( ( parent ) => ( <li><Link to={ '/blueprint/' + parent }>{ parent }</Link></li> ) ) }</ul></td></tr>
                  <tr><th>Description</th><td>{ blueprint.description }</td></tr>
                  <tr><th>Config Values</th><td><table><thead/><tbody>{ blueprint.config_values.map( ( value ) => ( <tr key={ value[0] }><th>{ value[0] }</th><td>{ value[1] }</td></tr> ) ) }</tbody></table></td></tr>
                  <tr><th>Scripts</th><td><ul>{ blueprint.scripts.map( ( script, index ) => ( <li key={ index } >{ script } <ScriptDialog getScript={ this.props.getScript } id={ script }/></li> ) ) }</ul></td></tr>
                  { blueprint.foundation_blueprint_list !== undefined &&
                    <tr><th >Foundation Blueprint</th><td><ul>
                    {
                      blueprint.foundation_blueprint_list.map( ( item, index ) => ( <li key={ index } ><Link to={ '/blueprint/f/' + CInP.extractIds( item )[0] }>{ CInP.extractIds( item )[0] }</Link></li> ) )
                    }
                    </ul></td></tr>
                  }
                  { blueprint.foundation_type_list !== undefined &&
                    <tr><th>Type List</th><td>{ blueprint.foundation_type_list }</td></tr>
                  }
                  { blueprint.template !== undefined &&
                    <tr><th>Template</th><td>{ JSON.stringify( blueprint.template ) }</td></tr>
                  }
                  { blueprint.physical_interface_names !== undefined &&
                    <tr><th>Physical Interface Names</th><td>{ blueprint.physical_interface_names }</td></tr>
                  }
                  <tr><th>Created</th><td>{ blueprint.created }</td></tr>
                  <tr><th>Updated</th><td>{ blueprint.updated }</td></tr>
                </tbody>
              </table>
            </div>
          }
        </div>
      );
    }

    return (
      <div>
        <h3>Foundation BluePrints</h3>
        <Table selectable={ false } multiSelectable={ false }>
          <TableHead>
            <TableCell>Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableHead>
          { this.state.blueprintF_list.map( ( item ) => (
            <TableRow key={ item.name }>
              <TableCell><Link to={ '/blueprint/f/' + item.name }>{ item.name }</Link></TableCell>
              <TableCell>{ item.description }</TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </Table>
        <h3>Structure BluePrints</h3>
        <Table selectable={ false } multiSelectable={ false }>
          <TableHead>
            <TableCell>Name</TableCell>
            <TableCell>Description</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableHead>
          { this.state.blueprintS_list.map( ( item ) => (
            <TableRow key={ item.name }>
              <TableCell><Link to={ '/blueprint/s/' + item.name }>{ item.name }</Link></TableCell>
              <TableCell>{ item.description }</TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </Table>
      </div>
    );

  }
};

export default BluePrint;
