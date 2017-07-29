import React from 'react';
import CInP from './cinp';
import { Table, TableHead, TableRow, TableCell, Dropdown, Checkbox, List, ListItem, ListCheckbox } from 'react-toolbox';
import { Link } from 'react-router-dom';


class Todo extends React.Component
{
  constructor( props )
  {
    super( props );
    this.props.classListGet()
    .then( ( result ) =>
    {
      var foundationClass_list = []
      foundationClass_list.push( { value: null, label: '<All>' } )
      for ( var index in result.data )
      {
        foundationClass_list.push( { value: result.data[ index ], label: result.data[ index ] } );
      }

      this.setState( { foundationClass_list: foundationClass_list} );
    } );
  }

  state = {
      foundation_list: [],
      foundationClass_list: [],
      isAutoBuild: true,
      hasDependancies: false,
      foundationClass: null
  };

  handleOptionChange = ( field, value ) =>
  {
    this.setState( { [ field ]: value }, () => this.update( this.props ) );
  };

  handleClassChange = ( value ) =>
  {
    this.setState( { foundationClass: value }, () => this.update( this.props ) );
  };

  componentDidMount()
  {
    this.update( this.props );
  };

  componentWillReceiveProps( newProps )
  {
    this.setState( { foundation_list: [] } );
    this.update( newProps );
  }

  update( props )
  {
    props.listGet( props.site, this.state.isAutoBuild, this.state.hasDependancies, this.state.foundationClass )
      .then( ( result ) =>
      {
        var foundation_list = [];
        for ( var id in result.data )
        {
          var foundation = result.data[ id ];
          id = CInP.extractIds( id )[0];
          foundation_list.push( { id: id,
                                  locator: foundation.locator,
                                  autoBuild: foundation.can_auto_locate,
                                  dependancyCount: ' ',
                                  complex: ' ',
                                  created: foundation.created,
                                  updated: foundation.updated
                                } );
        }

        this.setState( { foundation_list: foundation_list } );
      } );
  }

  render()
  {
    return (
      <div>
        <List>
          <ListCheckbox checked={ this.state.isAutoBuild } onChange={ this.handleOptionChange.bind( this, 'isAutoBuild' ) } caption="Auto Build"/>
          <ListCheckbox checked={ this.state.hasDependancies } onChange={ this.handleOptionChange.bind( this, 'hasDependancies' ) } caption="Has Dependancies"/>
          <ListItem caption="Foundation Class">
             <Dropdown auto onChange={ this.handleClassChange } source={ this.state.foundationClass_list } value={ this.state.foundationClass } allowBlank={false} />
          </ListItem>
        </List>
        <Table selectable={ false } multiSelectable={ false }>
          <TableHead>
            <TableCell numeric>Id</TableCell>
            <TableCell>Locator</TableCell>
            <TableCell>Is Auto Build</TableCell>
            <TableCell>Num Dependants</TableCell>
            <TableCell>Complex</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Updated</TableCell>
          </TableHead>
          { this.state.foundation_list.map( ( item ) => (
            <TableRow key={ item.id }>
              <TableCell numeric><Link to={ '/foundation/' + item.id }>{ item.id }</Link></TableCell>
              <TableCell>{ item.locator }</TableCell>
              <TableCell>{ item.autoBuild }</TableCell>
              <TableCell>{ item.dependancyCount }</TableCell>
              <TableCell>{ item.complex }</TableCell>
              <TableCell>{ item.created }</TableCell>
              <TableCell>{ item.updated }</TableCell>
            </TableRow>
          ) ) }
        </Table>
      </div>
    );

  }
};

export default Todo;
